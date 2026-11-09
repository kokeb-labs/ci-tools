// Near miss: the derived class adds an overload and names the base overload set in a using-declaration, and the
// base has a single function of that name.
#ifndef KV_RULE_6_4_2_USING_OK_NEAR_HPP
#define KV_RULE_6_4_2_USING_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_6_4_2_using::near {

class Base {
 public:
  std::int32_t scale(std::int32_t v) const { return v; }
};

class Derived : public Base {
 public:
  using Base::scale;
  std::int32_t scale(std::int16_t v) const { return static_cast<std::int32_t>(v) * 2; }
};

inline std::int32_t use(Derived const& d) { return d.scale(std::int16_t{3}) + d.scale(std::int32_t{4}); }

}  // namespace kv::rule_6_4_2_using::near

#endif  // KV_RULE_6_4_2_USING_OK_NEAR_HPP
