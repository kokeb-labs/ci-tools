// Seeded violation (member): a scoped enumeration declared inside a class with no fixed type.
#include <cstdint>

namespace kv::rule_10_2_1::bad_member {

class Motor {
 public:
  enum class State { kOff, kOn };
  State state() const { return state_; }

 private:
  State state_ = State::kOff;
};

}  // namespace kv::rule_10_2_1::bad_member
