// Seeded violation: C string functions on raw character pointers.
#include <cstddef>
#include <cstdlib>
#include <cstring>

namespace kv::rule_21_2_2::bad {

std::size_t length(const char* text) { return std::strlen(text); }  // seeded

void copy(char* dest, const char* source) { std::strcpy(dest, source); }  // seeded

long to_number(const char* text) { return std::strtol(text, nullptr, 10); }  // seeded

}  // namespace kv::rule_21_2_2::bad
