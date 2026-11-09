// Seeded violation: a destructor function-try-block handler reads a member.
namespace kv::rule_18_3_3::bad_dtor {

class Port {
 public:
  ~Port() try {  // seeded: clang
  } catch (...) {  // seeded: gcc
    last_ = id_;
  }

 private:
  int id_ = 1;
  static int last_;
};

int Port::last_ = 0;

}  // namespace kv::rule_18_3_3::bad_dtor
