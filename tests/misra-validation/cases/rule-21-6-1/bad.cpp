// Seeded violation: storage obtained from the heap.
#include <cstdint>
#include <cstdlib>

namespace kv::rule_21_6_1::bad {

std::int32_t* make_counter() { return new std::int32_t{0}; }

void* raw_block() { return std::malloc(16U); }

}  // namespace kv::rule_21_6_1::bad
