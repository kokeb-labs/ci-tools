// Seeded violation: an array new-expression and calloc / realloc.
#include <cstddef>
#include <cstdint>
#include <cstdlib>

namespace kv::rule_21_6_1::bad_array_new {

std::uint8_t* make_buffer(std::size_t n) { return new std::uint8_t[n]; }

void* grow(void* block, std::size_t n) { return std::realloc(block, n); }

void* zeroed(std::size_t n) { return std::calloc(n, 1U); }

}  // namespace kv::rule_21_6_1::bad_array_new
