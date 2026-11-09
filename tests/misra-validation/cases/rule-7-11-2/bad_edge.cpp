// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_7_11_2::bad_edge {

inline std::int32_t first(std::int32_t const* values) { return values[0]; }

struct Frame {
  std::int32_t words[2]{};
};

std::int32_t from_member(Frame const& f) { return first(f.words); }

template <typename T>
T head(T const* p) {
  return *p;
}

std::int32_t from_template() {
  std::int32_t const local[2] = {4, 5};
  return head(local);
}

}  // namespace kv::rule_7_11_2::bad_edge
