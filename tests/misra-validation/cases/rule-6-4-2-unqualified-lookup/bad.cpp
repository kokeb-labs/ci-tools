// Seeded violation: a using-declaration does not bring in a base overload whose signature the derived class
// redeclares, so that base overload stays concealed.
#include <cstdint>

namespace kv::rule_6_4_2_lookup::bad {

class Base {
 public:
  std::int32_t convert(std::int32_t v) const { return v; }
  std::int32_t convert(std::int16_t v) const { return static_cast<std::int32_t>(v); }
};

class Derived : public Base {
 public:
  using Base::convert;  // introduces convert(std::int16_t) only
  std::int32_t convert(std::int32_t v) const { return v + 1; }  // seeded
};

std::int32_t use(Derived const& d) { return d.convert(std::int32_t{5}); }

}  // namespace kv::rule_6_4_2_lookup::bad
