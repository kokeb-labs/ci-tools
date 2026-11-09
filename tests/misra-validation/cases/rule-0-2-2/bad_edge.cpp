// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_0_2_2::bad_edge {

class Filter {
 public:
  std::uint32_t apply(std::uint32_t value, std::uint32_t gain) const { return value; }  // seeded
};

std::uint32_t via_lambda(std::uint32_t v) {
  const auto f = [](std::uint32_t x, std::uint32_t ignored) { return x; };  // seeded
  return f(v, 2U);
}

template <typename T>
T first(T a, T b) {  // seeded
  return a;
}
template std::uint32_t first<std::uint32_t>(std::uint32_t, std::uint32_t);

}  // namespace kv::rule_0_2_2::bad_edge
