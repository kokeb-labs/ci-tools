#ifndef KV_RULE_6_4_2_NONVIRTUAL_OK_HPP
#define KV_RULE_6_4_2_NONVIRTUAL_OK_HPP

// Compliant: the derived class brings the base overload into scope with a using-declaration.
#include <cstdint>

namespace kv::rule_6_4_2_nonvirtual::ok {

class Base {
 public:
  std::int32_t level() const { return 1; }
};

class Derived : public Base {
 public:
  using Base::level;
  std::int32_t level(std::int32_t bias) const { return bias; }
};

inline bool use(Derived const& d) { return d.level(2) == d.level(); }

}  // namespace kv::rule_6_4_2_nonvirtual::ok

#endif  // KV_RULE_6_4_2_NONVIRTUAL_OK_HPP
