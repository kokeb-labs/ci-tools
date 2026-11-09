// Seeded violation: an object built with placement new and ended by an explicit destructor call.
#include <cstddef>
#include <cstdint>
#include <new>

namespace kv::rule_21_6_3::bad {

struct Item {
  std::int32_t value;
};

std::int32_t build_in_place() {
  alignas(Item) std::byte storage[sizeof(Item)];
  Item* item = new (storage) Item{5};
  const std::int32_t result = item->value;
  item->~Item();
  return result;
}

}  // namespace kv::rule_21_6_3::bad
