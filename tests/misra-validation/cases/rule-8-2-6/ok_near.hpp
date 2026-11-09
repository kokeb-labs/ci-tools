// Near misses: compliant code close to a violation.
#ifndef KV_RULE_8_2_6_OK_NEAR_HPP
#define KV_RULE_8_2_6_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_8_2_6::ok_near {

inline constexpr std::uintptr_t kStatusAddress = 0x40001000U;

inline void const* erase(std::uint32_t const* p) { return static_cast<void const*>(p); }

inline std::uint32_t const* none() { return nullptr; }

inline bool aligned(std::uintptr_t address) { return (address & 0x3U) == 0U; }

}  // namespace kv::rule_8_2_6::ok_near

#endif  // KV_RULE_8_2_6_OK_NEAR_HPP
