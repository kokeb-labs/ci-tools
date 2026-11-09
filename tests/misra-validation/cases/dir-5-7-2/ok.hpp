// Compliant: comments describe, they do not hold code.
#ifndef KV_DIR_5_7_2_OK_HPP
#define KV_DIR_5_7_2_OK_HPP

#include <cstdint>

namespace kv::dir_5_7_2::ok {

// Doubles the value; a shift keeps it in unsigned arithmetic.
inline std::uint32_t scale(std::uint32_t v) { return v << 1U; }

}  // namespace kv::dir_5_7_2::ok

#endif  // KV_DIR_5_7_2_OK_HPP
