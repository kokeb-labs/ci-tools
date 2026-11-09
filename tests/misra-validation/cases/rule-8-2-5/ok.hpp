// Compliant: std::bit_cast copies the representation without a reinterpret_cast.
#ifndef KV_RULE_8_2_5_OK_HPP
#define KV_RULE_8_2_5_OK_HPP

#include <bit>
#include <cstdint>

namespace kv::rule_8_2_5::ok {

inline std::uint32_t bits_of(float value) { return std::bit_cast<std::uint32_t>(value); }

}  // namespace kv::rule_8_2_5::ok

#endif  // KV_RULE_8_2_5_OK_HPP
