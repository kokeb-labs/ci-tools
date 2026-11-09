// Near miss: nested conditional groups, all closed.
#ifndef KV_RULE_19_1_2_OK_NESTED_HPP
#define KV_RULE_19_1_2_OK_NESTED_HPP

#include <cstdint>

namespace kv::rule_19_1_2::ok_nested {

#if defined(KV_FEATURE)
#ifdef KV_FEATURE_FAST
constexpr std::uint8_t kSpeed = 2U;
#else
constexpr std::uint8_t kSpeed = 1U;
#endif
#else
constexpr std::uint8_t kSpeed = 0U;
#endif

}  // namespace kv::rule_19_1_2::ok_nested

#endif  // KV_RULE_19_1_2_OK_NESTED_HPP
