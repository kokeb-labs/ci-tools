// Compliant: defined written directly in #elif.
#ifndef KV_RULE_19_1_1_ELIF_OK_HPP
#define KV_RULE_19_1_1_ELIF_OK_HPP

#include <cstdint>

namespace kv::rule_19_1_1_elif::ok {

#if 0
constexpr std::uint8_t kDebug = 2U;
#elif defined(KV_DEBUG)
constexpr std::uint8_t kDebug = 1U;
#else
constexpr std::uint8_t kDebug = 0U;
#endif

}  // namespace kv::rule_19_1_1_elif::ok

#endif  // KV_RULE_19_1_1_ELIF_OK_HPP
