#ifndef KV_RULE_6_2_4_OK_HPP
#define KV_RULE_6_2_4_OK_HPP

// Compliant: the header's function and object are inline.
#include <cstdint>

namespace kv::rule_6_2_4::ok {

inline std::uint32_t twice(std::uint16_t v) { return static_cast<std::uint32_t>(v) * 2U; }

inline constexpr std::int32_t kScale{4};

}  // namespace kv::rule_6_2_4::ok

#endif  // KV_RULE_6_2_4_OK_HPP
