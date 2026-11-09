// Seeded violation: an unqualified call in a class template finds the namespace function, not the
// member of the dependent base with the same name.
#include <cstdint>

namespace kv::rule_6_4_3::bad {

std::int32_t gain() { return 1; }

template <typename T>
struct Base {
  std::int32_t gain() const { return 2; }
  T value{};
};

template <typename T>
struct Channel : Base<T> {
  std::int32_t scaled() const { return gain(); }  // seeded
};

std::int32_t use() { return Channel<std::int32_t>{}.scaled(); }

}  // namespace kv::rule_6_4_3::bad
