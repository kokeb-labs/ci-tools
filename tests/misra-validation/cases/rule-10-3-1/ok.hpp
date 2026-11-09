// Compliant: the header uses a named detail namespace instead.
#ifndef KV_RULE_10_3_1_OK_HPP
#define KV_RULE_10_3_1_OK_HPP

#include <cstdint>

namespace kv::rule_10_3_1::ok {
namespace detail {

inline constexpr std::uint32_t kLimit = 8U;

}  // namespace detail

inline std::uint32_t limit() { return detail::kLimit; }

}  // namespace kv::rule_10_3_1::ok

#endif  // KV_RULE_10_3_1_OK_HPP
