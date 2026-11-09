// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_8_18_2::bad_edge {

inline std::uint32_t id(std::uint32_t v) { return v; }

std::uint32_t chained(std::uint32_t& a, std::uint32_t& b, std::uint32_t c) {
  a = b = c;
  return a;
}

std::uint32_t argument(std::uint32_t& x) { return id(x = 3U); }

std::uint32_t compound(std::uint32_t& x) { return x += 1U; }

std::uint32_t drain(std::uint32_t const* p) {
  std::uint32_t v = 0U;
  std::uint32_t n = 0U;
  while ((v = *p) != 0U) {
    n = v;
    break;
  }
  return n;
}

}  // namespace kv::rule_8_18_2::bad_edge
