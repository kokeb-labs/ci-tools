// Seeded violation: uninitialized storage filled with std::uninitialized_fill_n.
#include <cstddef>
#include <cstdint>
#include <memory>

namespace kv::rule_21_6_3_uninitialized::bad_uninitialized {

std::int32_t fill_raw() {
  alignas(std::int32_t) std::byte storage[4U * sizeof(std::int32_t)];
  std::int32_t* first = reinterpret_cast<std::int32_t*>(storage);
  static_cast<void>(std::uninitialized_fill_n(first, 4U, 9));  // seeded
  return first[0];
}

}  // namespace kv::rule_21_6_3_uninitialized::bad_uninitialized
