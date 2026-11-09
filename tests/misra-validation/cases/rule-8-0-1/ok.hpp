// Compliant: the operand of each operator of a different precedence is parenthesised.
#ifndef KV_RULE_8_0_1_OK_HPP
#define KV_RULE_8_0_1_OK_HPP

#include <cstdint>
#include <cstddef>

namespace kv::rule_8_0_1::ok {

inline std::uint32_t pack(std::uint32_t high, std::uint32_t low) { return (high << 8U) + low; }

inline std::size_t width(std::uint32_t value) { return sizeof(value); }

}  // namespace kv::rule_8_0_1::ok

#endif  // KV_RULE_8_0_1_OK_HPP
