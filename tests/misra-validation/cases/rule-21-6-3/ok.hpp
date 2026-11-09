// Compliant: an ordinary object whose lifetime the language manages.
#ifndef KV_RULE_21_6_3_OK_HPP
#define KV_RULE_21_6_3_OK_HPP

#include <cstdint>

namespace kv::rule_21_6_3::ok {

struct Item {
  std::int32_t value;
};

[[nodiscard]] inline std::int32_t build() {
  const Item item{5};
  return item.value;
}

}  // namespace kv::rule_21_6_3::ok

#endif  // KV_RULE_21_6_3_OK_HPP
