// Compliant: the #if group opens and closes in this file.
#ifndef KV_RULE_19_1_2_OK_HPP
#define KV_RULE_19_1_2_OK_HPP

#include <cstdint>

#if defined(KV_FEATURE)
namespace kv::rule_19_1_2::ok {

constexpr std::uint8_t kValue = 1U;

}  // namespace kv::rule_19_1_2::ok
#endif

#endif  // KV_RULE_19_1_2_OK_HPP
