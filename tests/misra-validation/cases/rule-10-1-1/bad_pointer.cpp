// Seeded violation (pointer): a pointer parameter whose pointee is only read.
#include <cstdint>

namespace kv::rule_10_1_1::bad_pointer {

std::int32_t first(std::int32_t* values) {  // seeded
  return values[0];
}

}  // namespace kv::rule_10_1_1::bad_pointer
