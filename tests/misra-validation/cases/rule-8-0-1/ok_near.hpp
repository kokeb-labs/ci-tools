// Near misses: compliant code close to a violation.
#ifndef KV_RULE_8_0_1_OK_NEAR_HPP
#define KV_RULE_8_0_1_OK_NEAR_HPP

#include <cstddef>
#include <cstdint>

namespace kv::rule_8_0_1::ok_near {

inline std::uint32_t combine(std::uint32_t a, std::uint32_t b, std::uint32_t c) { return (a & b) | c; }

inline std::uint32_t chain(std::uint32_t a, std::uint32_t b, std::uint32_t c) { return a + b + c; }

inline std::size_t width_of(std::uint32_t const* p) { return sizeof(*p); }

}  // namespace kv::rule_8_0_1::ok_near

#endif  // KV_RULE_8_0_1_OK_NEAR_HPP
