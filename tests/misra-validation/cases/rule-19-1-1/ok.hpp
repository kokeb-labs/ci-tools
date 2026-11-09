// Compliant: defined is written directly in the #if, in its two standard forms.
#ifndef KV_RULE_19_1_1_OK_HPP
#define KV_RULE_19_1_1_OK_HPP

#include <cstdint>

#if defined(KV_TRACE) || defined KV_TRACE_ALL
namespace kv::rule_19_1_1::ok {

constexpr std::uint8_t kTrace = 1U;

}  // namespace kv::rule_19_1_1::ok
#else
namespace kv::rule_19_1_1::ok {

constexpr std::uint8_t kTrace = 0U;

}  // namespace kv::rule_19_1_1::ok
#endif

#endif  // KV_RULE_19_1_1_OK_HPP
