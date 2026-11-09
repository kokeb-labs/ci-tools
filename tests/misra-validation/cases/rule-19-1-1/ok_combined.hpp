// Near miss: defined combined with other operators, written directly in #if and #elif.
#ifndef KV_RULE_19_1_1_OK_COMBINED_HPP
#define KV_RULE_19_1_1_OK_COMBINED_HPP

#include <cstdint>

namespace kv::rule_19_1_1::ok_combined {

#if defined(KV_FAST) && !defined(KV_SAFE)
constexpr std::uint8_t kMode = 1U;
#elif defined KV_SAFE
constexpr std::uint8_t kMode = 2U;
#else
constexpr std::uint8_t kMode = 0U;
#endif

}  // namespace kv::rule_19_1_1::ok_combined

#endif  // KV_RULE_19_1_1_OK_COMBINED_HPP
