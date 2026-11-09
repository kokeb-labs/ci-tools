// Near misses: compliant code that resembles a violation.
#ifndef KV_DIR_5_7_2_OK_NEAR_HPP
#define KV_DIR_5_7_2_OK_NEAR_HPP

#include <cstdint>

namespace kv::dir_5_7_2::near {

// Masks the value to its low three bits; values above seven lose their high bits.
// See the datasheet, section 7: the field is three bits wide.
inline std::uint32_t clamp(std::uint32_t v) { return v & 7U; }

}  // namespace kv::dir_5_7_2::near

#endif  // KV_DIR_5_7_2_OK_NEAR_HPP
