// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_8_2_11_trivial::bad_edge {

struct Owner {
  Owner() = default;
  Owner(Owner const&) = default;
  Owner& operator=(Owner const& other) {
    tag = other.tag;
    return *this;
  }
  std::int32_t tag{1};
};

std::int32_t take(std::int32_t count, ...);

std::int32_t use() {
  Owner o;
  return take(1, o);
}

}  // namespace kv::rule_8_2_11_trivial::bad_edge
