// Seeded violation: a class overloads the unary address-of operator.
#include <cstdint>

namespace kv::rule_16_5_2::bad {

class Register {
 public:
  std::uint32_t* operator&() { return &value_; }

 private:
  std::uint32_t value_ = 0U;
};

}  // namespace kv::rule_16_5_2::bad
