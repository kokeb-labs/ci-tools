// Compliant near miss: std::optional starts and ends the object's lifetime for us.
#ifndef KV_RULE_21_6_3_OK_OPTIONAL_HPP
#define KV_RULE_21_6_3_OK_OPTIONAL_HPP

#include <cstdint>
#include <optional>

namespace kv::rule_21_6_3::ok_optional {

struct Item {
  std::int32_t value;
};

[[nodiscard]] inline std::int32_t build_and_clear() {
  std::optional<Item> slot;
  static_cast<void>(slot.emplace(Item{5}));
  const std::int32_t result = slot->value;
  slot.reset();
  return result;
}

}  // namespace kv::rule_21_6_3::ok_optional

#endif  // KV_RULE_21_6_3_OK_OPTIONAL_HPP
