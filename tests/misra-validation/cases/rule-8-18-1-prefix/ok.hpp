// Compliant: no union; the halves are separate members.
#ifndef KV_RULE_8_18_1_PREFIX_OK_HPP
#define KV_RULE_8_18_1_PREFIX_OK_HPP

#include <cstdint>

namespace kv::rule_8_18_1_prefix::ok {

struct Word {
  std::uint32_t whole{0U};
  std::uint32_t low_half{0U};
};

inline std::uint32_t fold(Word& w) {
  w.whole = w.low_half;
  return w.whole;
}

}  // namespace kv::rule_8_18_1_prefix::ok

#endif  // KV_RULE_8_18_1_PREFIX_OK_HPP
