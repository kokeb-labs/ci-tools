// Compliant near miss: std::optional starts and ends the object's lifetime; no <memory> raw-storage function is called.
#ifndef KV_RULE_21_6_3_UNINITIALIZED_OK_HPP
#define KV_RULE_21_6_3_UNINITIALIZED_OK_HPP

#include <cstdint>
#include <optional>

namespace kv::rule_21_6_3_uninitialized::ok {

[[nodiscard]] inline std::int32_t take(std::optional<std::int32_t>& slot) {
  const std::int32_t value = slot.value_or(0);
  slot.reset();
  return value;
}

}  // namespace kv::rule_21_6_3_uninitialized::ok

#endif  // KV_RULE_21_6_3_UNINITIALIZED_OK_HPP
