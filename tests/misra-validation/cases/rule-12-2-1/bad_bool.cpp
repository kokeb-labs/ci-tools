// Seeded violation (bool): a bool bit-field in a class.
#include <cstdint>

namespace kv::rule_12_2_1::bad_bool {

class Status {
 public:
  bool ready() const { return ready_; }

 private:
  bool ready_ : 1 = false;  // seeded
};

}  // namespace kv::rule_12_2_1::bad_bool
