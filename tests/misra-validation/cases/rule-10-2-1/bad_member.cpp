// Seeded violation (member): a scoped enumeration inside a class, with a value given and no fixed type.
#include <cstdint>

namespace kv::rule_10_2_1::bad_member {

class Motor {
 public:
  enum class State { kOff, kOn = 4 };  // seeded
  State state() const { return state_; }

 private:
  State state_ = State::kOff;
};

}  // namespace kv::rule_10_2_1::bad_member
