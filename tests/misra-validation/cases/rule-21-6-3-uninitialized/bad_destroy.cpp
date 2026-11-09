// Seeded violation: objects made in raw storage with std::uninitialized_value_construct_n and ended with
// std::destroy_at (std::construct_at is not one of the listed functions, so it is not used here).
#include <cstddef>
#include <cstdint>
#include <memory>

namespace kv::rule_21_6_3_uninitialized::bad_destroy {

struct Item {
  std::int32_t value;
};

std::int32_t build_in_place() {
  alignas(Item) std::byte storage[sizeof(Item)];
  Item* const item = reinterpret_cast<Item*>(storage);
  static_cast<void>(std::uninitialized_value_construct_n(item, 1U));  // seeded
  const std::int32_t result = item->value;
  std::destroy_at(item);  // seeded
  return result;
}

}  // namespace kv::rule_21_6_3_uninitialized::bad_destroy
