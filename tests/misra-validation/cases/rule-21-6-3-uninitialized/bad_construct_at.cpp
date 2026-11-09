// Seeded violation: an object made with std::construct_at and ended with std::destroy_at.
#include <cstddef>
#include <cstdint>
#include <memory>

namespace kv::rule_21_6_3_uninitialized::bad_construct_at {

struct Item {
  std::int32_t value;
};

std::int32_t build_in_place() {
  alignas(Item) std::byte storage[sizeof(Item)];
  Item* item = std::construct_at(reinterpret_cast<Item*>(storage), Item{7});
  const std::int32_t result = item->value;
  std::destroy_at(item);
  return result;
}

}  // namespace kv::rule_21_6_3_uninitialized::bad_construct_at
