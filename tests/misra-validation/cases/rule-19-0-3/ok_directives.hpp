// Near miss: #include after #define and #if, before any declaration.
#ifndef KV_RULE_19_0_3_OK_DIRECTIVES_HPP
#define KV_RULE_19_0_3_OK_DIRECTIVES_HPP

#define KV_RULE_19_0_3_WIDE 1

#if KV_RULE_19_0_3_WIDE
#include <cstdint>
#endif

namespace kv::rule_19_0_3::ok_directives {

constexpr std::uint8_t kWide = KV_RULE_19_0_3_WIDE;

}  // namespace kv::rule_19_0_3::ok_directives

#undef KV_RULE_19_0_3_WIDE

#endif  // KV_RULE_19_0_3_OK_DIRECTIVES_HPP
