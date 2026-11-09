// Compliant: the identifier is defined before #if uses it, or tested with defined first.
#ifndef KV_RULE_19_1_3_OK_HPP
#define KV_RULE_19_1_3_OK_HPP

#include <cstdint>

#define KV_RULE_19_1_3_LEVEL 2

#if KV_RULE_19_1_3_LEVEL > 1
namespace kv::rule_19_1_3::ok {

constexpr std::uint8_t kVerbose = 1U;

}  // namespace kv::rule_19_1_3::ok
#endif

#if defined(KV_RULE_19_1_3_EXTRA) && (KV_RULE_19_1_3_EXTRA > 0)
namespace kv::rule_19_1_3::ok {
constexpr std::uint8_t kExtra = 1U;
}  // namespace kv::rule_19_1_3::ok
#endif

#undef KV_RULE_19_1_3_LEVEL

#endif  // KV_RULE_19_1_3_OK_HPP
