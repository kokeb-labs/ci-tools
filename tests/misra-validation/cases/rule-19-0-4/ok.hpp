// Compliant: the file only #undefs the macro it defined itself.
#ifndef KV_RULE_19_0_4_OK_HPP
#define KV_RULE_19_0_4_OK_HPP

#include <cstdint>

#define KV_RULE_19_0_4_LOCAL 1

namespace kv::rule_19_0_4::ok {

constexpr std::uint8_t kValue = KV_RULE_19_0_4_LOCAL;

}  // namespace kv::rule_19_0_4::ok

#undef KV_RULE_19_0_4_LOCAL

#endif  // KV_RULE_19_0_4_OK_HPP
