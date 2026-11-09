// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_8_2_1::bad_edge {

struct Base {
  virtual ~Base() = default;
  std::int32_t id{0};
};

struct Derived : virtual Base {  // seeded: clang-tidy
  std::int32_t extra{0};
};

std::int32_t from_const(Base const* b) {
  Derived const* d = reinterpret_cast<Derived const*>(b);  // seeded: codeql
  return d->extra;
}

std::int32_t by_reference(Base& b) { return reinterpret_cast<Derived&>(b).extra; }  // seeded: codeql

}  // namespace kv::rule_8_2_1::bad_edge
