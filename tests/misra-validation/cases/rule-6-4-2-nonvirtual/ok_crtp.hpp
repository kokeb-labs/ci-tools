// Near miss (CRTP): the derived class conceals a member of a base that is a template specialisation taking the
// derived class as its argument, which the guideline's exception allows (the pattern of our port bases).
#ifndef KV_RULE_6_4_2_NONVIRTUAL_OK_CRTP_HPP
#define KV_RULE_6_4_2_NONVIRTUAL_OK_CRTP_HPP

#include <cstdint>

namespace kv::rule_6_4_2_nonvirtual::crtp {

template <typename Derived>
class PortBase {
 public:
  std::int32_t transfer() { return self().hook(); }
  std::int32_t hook() { return 0; }

 private:
  Derived& self() { return static_cast<Derived&>(*this); }
};

class SpiPort : public PortBase<SpiPort> {
 public:
  std::int32_t hook() { return 1; }
};

inline std::int32_t use(SpiPort& p) { return p.transfer(); }

}  // namespace kv::rule_6_4_2_nonvirtual::crtp

#endif  // KV_RULE_6_4_2_NONVIRTUAL_OK_CRTP_HPP
