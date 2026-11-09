// Seeded violation: heap memory owned through a raw pointer and released by hand.
#include <cstdint>
#include <cstdlib>

namespace kv::rule_21_6_2::bad {

std::int32_t compute() {
  std::int32_t* value = new std::int32_t{3};
  const std::int32_t result = *value;
  delete value;
  return result;
}

void scratch() {
  void* block = std::malloc(8U);
  std::free(block);
}

}  // namespace kv::rule_21_6_2::bad
