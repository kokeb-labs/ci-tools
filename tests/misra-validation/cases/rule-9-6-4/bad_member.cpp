// Seeded violation (member): a [[noreturn]] member function with an explicit return.
#include <cstdint>

namespace kv::rule_9_6_4::bad_member {

class Fault {
 public:
  [[noreturn]] void raise(std::int32_t code) {  // seeded
    code_ = code;
    if (code_ != 0) {
      for (;;) {
      }
    }
    return;
  }

 private:
  std::int32_t code_ = 0;
};

}  // namespace kv::rule_9_6_4::bad_member
