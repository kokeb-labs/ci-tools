// Seeded violation: the address of strlen taken and called through the pointer.
#include <cstddef>
#include <cstring>

namespace kv::rule_21_2_2::bad_address {

std::size_t measure(const char* text) {
  std::size_t (*const length)(const char*) = &std::strlen;
  return length(text);
}

}  // namespace kv::rule_21_2_2::bad_address
