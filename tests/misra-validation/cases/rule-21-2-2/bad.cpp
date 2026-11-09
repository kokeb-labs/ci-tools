// Seeded violation: C string functions on raw character pointers.
#include <cstddef>
#include <cstdlib>
#include <cstring>

namespace kv::rule_21_2_2::bad {

std::size_t length(const char* text) { return std::strlen(text); }

void copy(char* dest, const char* source) { std::strcpy(dest, source); }

long to_number(const char* text) { return std::strtol(text, nullptr, 10); }

}  // namespace kv::rule_21_2_2::bad
