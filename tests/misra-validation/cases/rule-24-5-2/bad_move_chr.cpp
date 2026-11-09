// Seeded violation: memmove and memchr through <string.h>, and memset's neighbour memcpy in a template.
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <string.h>

namespace kv::rule_24_5_2::bad_move_chr {

void shift(std::uint8_t* data, std::size_t n) { static_cast<void>(memmove(data, data + 1, n)); }

bool has_zero(const std::uint8_t* data, std::size_t n) { return ::memchr(data, 0, n) != nullptr; }

template <typename T>
void raw_copy(T& dest, const T& source) {
  static_cast<void>(std::memcpy(&dest, &source, sizeof(T)));
}

void use(std::uint32_t& a, const std::uint32_t& b) { raw_copy(a, b); }

}  // namespace kv::rule_24_5_2::bad_move_chr
