// Seeded violation: an object declared with three levels of pointer.
#include <cstdint>

namespace kv::rule_11_3_2::bad {

std::int32_t deref3(std::int32_t*** p) {  // seeded
  return ***p;
}

}  // namespace kv::rule_11_3_2::bad
