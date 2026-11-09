// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_8_2_11_trivial::bad_edge {

struct Owner {
  Owner() = default;
  Owner(Owner const&) = default;
  Owner(Owner&& other) noexcept : tag(other.tag) {}
  Owner& operator=(Owner const&) = default;
  Owner& operator=(Owner&&) = default;
  ~Owner() = default;
  std::int32_t tag{1};
};

std::int32_t take(std::int32_t count, ...);

std::int32_t use() {
  Owner o;
  return take(1, o);  // seeded
}

}  // namespace kv::rule_8_2_11_trivial::bad_edge
