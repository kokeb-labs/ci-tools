// Compliant: the one-bit field uses an unsigned fixed-width alias.
#ifndef KV_RULE_12_2_3_ALIAS_OK_HPP
#define KV_RULE_12_2_3_ALIAS_OK_HPP

#include <cstdint>

namespace kv::rule_12_2_3_alias::ok {

struct Bits {
  std::uint8_t enabled : 1;
};

inline bool on(const Bits& b) { return b.enabled != 0U; }

}  // namespace kv::rule_12_2_3_alias::ok

#endif  // KV_RULE_12_2_3_ALIAS_OK_HPP
