//! Merchant League dice.
//!
//! A day's roll comes from every merchant's secret plus a public randomness
//! beacon (drand) round published after the reveal deadline. Each secret is
//! committed as an XRPL escrow locked to its SHA-256 hash (a PREIMAGE-SHA-256
//! crypto-condition) and revealed by finishing that escrow, so the ledger
//! checks every reveal and enforces the deadline.
//!
//! This crate has the crypto-condition encoding the escrows use
//! ([`condition_hex`], [`fulfillment_hex`]) and the escrow finish's fee
//! ([`finish_fee_drops`]). The roll itself, and the drand round rule and
//! signature check, arrive with milestone M3.

use sha2::{Digest, Sha256};

/// A merchant's 32-byte secret for one day's roll. Never logged or shown.
#[derive(Clone, PartialEq, Eq)]
pub struct Secret(pub [u8; 32]);

impl std::fmt::Debug for Secret {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str("Secret(<hidden>)")
    }
}

/// A drand round number, named by the rules before reveals open.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub struct BeaconRound(pub u64);

/// The longest preimage this encoding handles: its length must fit in one
/// DER length byte. The game's secrets are 32 bytes.
pub const MAX_PREIMAGE_LEN: usize = 127;

/// A preimage longer than [`MAX_PREIMAGE_LEN`] bytes.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct PreimageTooLong(pub usize);

impl std::fmt::Display for PreimageTooLong {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "a preimage of {} bytes is longer than the {MAX_PREIMAGE_LEN} this encoding handles",
            self.0
        )
    }
}

impl std::error::Error for PreimageTooLong {}

/// The PREIMAGE-SHA-256 condition for `preimage`, as the uppercase hex an
/// `EscrowCreate`'s `Condition` field takes.
///
/// DER: `A0 25 80 20 <sha256(preimage)> 81 01 <length of preimage>`.
pub fn condition_hex_for(preimage: &[u8]) -> Result<String, PreimageTooLong> {
    let len = checked_len(preimage)?;
    let digest = Sha256::digest(preimage);
    let mut der = Vec::with_capacity(39);
    der.extend_from_slice(&[0xA0, 0x25, 0x80, 0x20]);
    der.extend_from_slice(&digest);
    der.extend_from_slice(&[0x81, 0x01, len]);
    Ok(upper_hex(&der))
}

/// The PREIMAGE-SHA-256 fulfillment for `preimage`, as the uppercase hex an
/// `EscrowFinish`'s `Fulfillment` field takes.
///
/// DER: `A0 <2 + length> 80 <length> <preimage>`.
pub fn fulfillment_hex_for(preimage: &[u8]) -> Result<String, PreimageTooLong> {
    let len = checked_len(preimage)?;
    let mut der = Vec::with_capacity(4 + preimage.len());
    der.extend_from_slice(&[0xA0, len + 2, 0x80, len]);
    der.extend_from_slice(preimage);
    Ok(upper_hex(&der))
}

/// The condition for a merchant's secret.
pub fn condition_hex(secret: &Secret) -> String {
    // 32 bytes always fits.
    condition_hex_for(&secret.0).unwrap_or_default()
}

/// The fulfillment for a merchant's secret. This reveals the secret.
pub fn fulfillment_hex(secret: &Secret) -> String {
    fulfillment_hex_for(&secret.0).unwrap_or_default()
}

/// The minimum fee, in drops, for an `EscrowFinish` that carries a
/// fulfillment: 330 drops plus 10 for every 16 bytes of preimage, at the
/// network's base fee of 10 drops (xrpl.org, EscrowFinish).
pub fn finish_fee_drops(preimage_len: usize) -> u64 {
    330 + 10 * preimage_len.div_ceil(16) as u64
}

fn checked_len(preimage: &[u8]) -> Result<u8, PreimageTooLong> {
    u8::try_from(preimage.len())
        .ok()
        .filter(|len| usize::from(*len) <= MAX_PREIMAGE_LEN)
        .ok_or(PreimageTooLong(preimage.len()))
}

fn upper_hex(bytes: &[u8]) -> String {
    const DIGITS: &[u8; 16] = b"0123456789ABCDEF";
    let mut out = String::with_capacity(bytes.len() * 2);
    for b in bytes {
        out.push(char::from(DIGITS[usize::from(b >> 4)]));
        out.push(char::from(DIGITS[usize::from(b & 0x0F)]));
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_secret_never_prints_its_bytes() {
        let secret = Secret([0xAB; 32]);
        let shown = format!("{secret:?}");
        assert_eq!(shown, "Secret(<hidden>)");
        assert!(!shown.to_lowercase().contains("ab"));
    }

    #[test]
    fn beacon_rounds_order_by_number() {
        assert!(BeaconRound(10) < BeaconRound(11));
    }

    /// The example on xrpl.org's EscrowCreate and EscrowFinish pages: an
    /// empty preimage.
    #[test]
    fn the_empty_preimage_matches_xrpl_org() -> Result<(), PreimageTooLong> {
        assert_eq!(
            condition_hex_for(&[])?,
            "A0258020E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855810100"
        );
        assert_eq!(fulfillment_hex_for(&[])?, "A0028000");
        Ok(())
    }

    /// Computed independently (Python hashlib) for the bytes 0, 1, ..., 31.
    #[test]
    fn a_32_byte_secret_matches_an_independent_encoding() {
        let mut bytes = [0u8; 32];
        for (i, b) in bytes.iter_mut().enumerate() {
            *b = i as u8;
        }
        let secret = Secret(bytes);
        assert_eq!(
            condition_hex(&secret),
            "A0258020630DCD2966C4336691125448BBB25B4FF412A49C732DB2C8ABC1B8581BD710DD810120"
        );
        assert_eq!(
            fulfillment_hex(&secret),
            "A0228020000102030405060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E1F"
        );
    }

    #[test]
    fn a_preimage_too_long_is_refused() {
        let long = [0u8; 128];
        assert_eq!(condition_hex_for(&long), Err(PreimageTooLong(128)));
        assert_eq!(fulfillment_hex_for(&long), Err(PreimageTooLong(128)));
        assert!(PreimageTooLong(128).to_string().contains("128 bytes"));
        assert!(condition_hex_for(&[0u8; 127]).is_ok());
    }

    #[test]
    fn secrets_and_errors_compare_and_copy() {
        let secret = Secret([7; 32]);
        assert_eq!(secret.clone(), secret);
        assert_ne!(Secret([8; 32]), secret);
        let err = PreimageTooLong(200);
        let copy = err;
        assert_eq!(copy, err);
        assert_eq!(format!("{err:?}"), "PreimageTooLong(200)");
    }

    #[test]
    fn the_finish_fee_follows_xrpl_org() {
        assert_eq!(finish_fee_drops(0), 330);
        assert_eq!(finish_fee_drops(32), 350);
        assert_eq!(finish_fee_drops(33), 360);
    }
}
