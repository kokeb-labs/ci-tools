// Compliant: the class is complete where its owner deletes it.
#ifndef KV_RULE_21_6_5_OK_HPP
#define KV_RULE_21_6_5_OK_HPP

#include <cstdint>
#include <memory>

namespace kv::rule_21_6_5::ok {

struct Complete {
  std::int32_t value;
};

[[nodiscard]] inline std::int32_t release(std::unique_ptr<Complete>& owner) {
  const std::int32_t last = (owner != nullptr) ? owner->value : 0;
  owner.reset();
  return last;
}

}  // namespace kv::rule_21_6_5::ok

#endif  // KV_RULE_21_6_5_OK_HPP
